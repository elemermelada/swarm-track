from tudatpy.kernel.interface import spice

import numpy as np
import json
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt

from util.math import fix_angle

# plt.rcParams["text.usetex"] = True


def plot_trajectory_parameters(
    axes,
    time,
    pos,
    vel,
    kep,
    selector=(0, -1, 1),
    scatter=False,
    linewidth=2,
    markersize=4,
):
    mode = "-"
    if scatter:
        mode = "x"
    axes[-2].plot(
        time[selector[0] : selector[1] : selector[2]],
        pos[selector[0] : selector[1] : selector[2], 0],
        mode,
        linewidth=linewidth,
        markersize=markersize,
        label="r",
    )
    axes[-2].plot(
        time[selector[0] : selector[1] : selector[2]],
        pos[selector[0] : selector[1] : selector[2], 1],
        mode,
        linewidth=linewidth,
        markersize=markersize,
        label="s",
    )
    axes[-2].plot(
        time[selector[0] : selector[1] : selector[2]],
        pos[selector[0] : selector[1] : selector[2], 2],
        mode,
        linewidth=linewidth,
        markersize=markersize,
        label="h",
    )
    axes[-2].title.set_text("Position")
    axes[-1].plot(
        time[selector[0] : selector[1] : selector[2]],
        vel[selector[0] : selector[1] : selector[2], 0],
        mode,
        linewidth=linewidth,
        markersize=markersize,
        label="r",
    )
    axes[-1].plot(
        time[selector[0] : selector[1] : selector[2]],
        vel[selector[0] : selector[1] : selector[2], 1],
        mode,
        linewidth=linewidth,
        markersize=markersize,
        label="s",
    )
    axes[-1].plot(
        time[selector[0] : selector[1] : selector[2]],
        vel[selector[0] : selector[1] : selector[2], 2],
        mode,
        linewidth=linewidth,
        markersize=markersize,
        label="h",
    )
    axes[-1].title.set_text("Velocity")
    axes[-2].legend()
    axes[-1].legend()

    axes[0].plot(
        time[selector[0] : selector[1] : selector[2]],
        kep[selector[0] : selector[1] : selector[2], 0],
        mode,
        linewidth=linewidth,
        markersize=markersize,
    )
    axes[0].title.set_text("a")
    axes[1].plot(
        time[selector[0] : selector[1] : selector[2]],
        kep[selector[0] : selector[1] : selector[2], 1],
        mode,
        linewidth=linewidth,
        markersize=markersize,
    )
    axes[1].title.set_text("e")
    axes[2].plot(
        time[selector[0] : selector[1] : selector[2]],
        kep[selector[0] : selector[1] : selector[2], 2],
        mode,
        linewidth=linewidth,
        markersize=markersize,
    )
    axes[2].title.set_text("i")
    axes[3].plot(
        time[selector[0] : selector[1] : selector[2]],
        kep[selector[0] : selector[1] : selector[2], 3],
        mode,
        linewidth=linewidth,
        markersize=markersize,
    )
    axes[3].title.set_text(r"\omega")
    axes[4].plot(
        time[selector[0] : selector[1] : selector[2]],
        kep[selector[0] : selector[1] : selector[2], 4],
        mode,
        linewidth=linewidth,
        markersize=markersize,
    )
    axes[4].title.set_text(r"\Omega")
    axes[5].plot(
        time[selector[0] : selector[1] : selector[2]],
        kep[selector[0] : selector[1] : selector[2], 5],
        mode,
        linewidth=linewidth,
        markersize=markersize,
    )
    axes[5].title.set_text(r"\theta")
    axes[6].plot(
        time[selector[0] : selector[1] : selector[2]],
        [
            fix_angle(
                kep[selector[0] : selector[1] : selector[2], 5][i]
                + kep[selector[0] : selector[1] : selector[2], 3][i],
                mode=2,
            )
            for i in range(len(kep[selector[0] : selector[1] : selector[2], 5]))
        ],
        mode,
        linewidth=linewidth,
        markersize=markersize,
    )
    axes[6].title.set_text(r"\theta + \omega")


def plot_ephemeris(
    ax: Axes, ephemeris, axis=[1, 2], threeD=False, color="b", linestyle="-"
):
    if threeD:
        ax.plot(
            ephemeris[:, 0],
            ephemeris[:, 1],
            ephemeris[:, 2],
            color=color,
            linestyle=linestyle,
            marker=".",
        )
        return ax
    ax.plot(
        ephemeris[:, axis[0]],
        ephemeris[:, axis[1]],
        color=color,
        linestyle=linestyle,
        marker=".",
    )
    return ax


def scatter_ephemeris(
    ax: Axes, ephemeris, axis=[1, 2], threeD=False, color="b", linestyle="-"
):
    if threeD:
        ax.scatter(
            ephemeris[:, 0],
            ephemeris[:, 1],
            ephemeris[:, 2],
            color=color,
            linestyle=linestyle,
            zorder=999,
        )
        return ax
    ax.scatter(
        ephemeris[:, axis[0]], ephemeris[:, axis[1]], color=color, linestyle=linestyle
    )
    return ax


def scatter_trajectory_from_spice(
    ax: Axes, body, timestamps, axis=[1, 2], threeD=False, color="b", linestyle="-"
):
    ephemeris = list()
    for epoch in timestamps:
        ephemeris.append(
            spice.get_body_cartesian_position_at_epoch(
                target_body_name=body,
                observer_body_name="Mars",
                reference_frame_name="J2000",
                aberration_corrections="none",
                ephemeris_time=epoch,
            )
        )
    ephemeris = np.array(ephemeris) * 1e-3
    return scatter_ephemeris(ax, ephemeris, axis, threeD, color, linestyle)


def plot_trajectory_from_spice(
    ax: Axes,
    body,
    simulation_start_epoch,
    simulation_end_epoch,
    axis=[1, 2],
    threeD=False,
    color="b",
    linestyle="-",
):
    time2plt = np.arange(simulation_start_epoch, simulation_end_epoch, 60)
    ephemeris = list()
    ephemeris_dict = dict()
    for epoch in time2plt:
        ephemeris.append(
            spice.get_body_cartesian_position_at_epoch(
                target_body_name=body,
                observer_body_name="Mars",
                reference_frame_name="J2000",
                aberration_corrections="none",
                ephemeris_time=epoch,
            )
        )
        ephemeris_dict[epoch] = (ephemeris[-1] * 1e-3).tolist()
    ephemeris = np.array(ephemeris) * 1e-3

    with open("out/spice.json", "w") as outfile:
        outfile.write(json.dumps(ephemeris_dict))

    return plot_ephemeris(ax, ephemeris, axis, threeD, color, linestyle)


def plot_mars(ax: Axes, threeD=False):
    radius_mars = spice.get_average_radius("Mars")
    if threeD:
        ax.scatter(0, 0, 0, color="firebrick")
        return ax
    ax.add_patch(
        plt.Circle((0, 0), radius_mars * 1e-3, color="firebrick", label="Mars")
    )
    return ax


def init_trajectory_graph(threeD=False):
    if threeD:
        fig = plt.figure()
        ax = fig.add_subplot(projection="3d")
        return (ax, fig)

    fig, ax = plt.subplots(1, 1, figsize=(9, 6))
    ax.axis("equal")
    ax.set_xlabel(r"$\Delta y$ [km]")
    ax.set_ylabel(r"$\Delta z$ [km]")
    ax.set_xlim(-1.0e4, 5.5e4)
    ax.set_ylim(-2.0e4, 2.0e4)
    ax.ticklabel_format(style="sci", scilimits=(0, 0), axis="both")

    return (ax, fig)


def init_observation_plot(n_axes=3):
    rows = int(np.ceil(np.sqrt(n_axes)))

    fig, axes = plt.subplots(
        rows,
        rows - 1 if rows * (rows - 1) >= n_axes else rows,
        figsize=(9 * 1.5, 6 * 1.5),
    )
    if n_axes == 1:
        return fig, [axes]

    axes = axes.reshape(rows * rows)
    for i in range(len(axes) - n_axes):
        axes[-1 - i].remove()

    return (fig, axes)


def plot_observations(
    ax: Axes,
    observations_object: dict,
    start_date,
    color="b",
    scatter=True,
    marker=None,
    title=None,
):
    observations = observations_object.values()
    times = np.array(list(observations_object.keys()))
    times = (times - start_date) / 86400
    if scatter:
        if marker is None:
            marker = "x"
        ax.plot(times, observations, marker, color=color, zorder=2.5, markersize=2)
    else:
        if marker is None:
            marker = "o-"
        ax.plot(times, observations, marker, color=color, markersize=3)
    if title:
        ax.set_title(title)

    # ax.set_xlim([0, 1])
    ax.set_xlabel("Time (days)")
